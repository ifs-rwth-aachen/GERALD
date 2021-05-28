<!--
*** Thanks for checking out this README Template. If you have a suggestion that would
*** make this better, please fork the repo and create a pull request or simply open
*** an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
-->





<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- GERSign LOGO -->

<div align="center">
  <a href="https://git.rwth-aachen.de/IFS/gersign">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Ks-Vorsignal_%28Ks_1%29.png/800px-Ks-Vorsignal_%28Ks_1%29.png" alt="Logo" width="80" height="140">
  </a>
</div>



  <div align="center">
  <small>
    “Ks-Vorsignal (Ks 1)”, by "Markus5linger", licensed under CC BY 4.0
  </small>
  </div>


  <h3 align="center">GERSign Dataset</h3>

  <div align="center">
    Dataset for German mainline railway light- and formsignals
  </div>



<!-- TABLE OF CONTENTS -->

## Table of Contents

* [About the Project](#about-the-project)
  * [Data format](#data-format)
  * [Data gathering](#how-the-data-was-gathered)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [Contributors](#contributors)
* [License](#license)
* [Contact](#contact)
* [Related datasets](#related-datasets)



<!-- ABOUT THE PROJECT -->
## About The Project



<div align="center">
  <a href="https://github.com/ifs-rwth-aachen/GERSign">
    <img src="https://github.com/ifs-rwth-aachen/GERSign/-/raw/master/assets/sunny_example_1.jpg" alt="Screenshot" width="600">
  </a>    
</div>


The German mainline railway form- und lightsignal dataset (GERSign) contains 3562 individual images with 25820 labelled bounding boxes  for many types of signals. Our first goal was to achieve at least 500 labelled instances for the following signal types:

* H/V system: Hp 0 (HV), Hp 1, Hp 2, Vr 0, Vr 1, Vr 2
* Ks system: Hp 0 (Ks), Ks 1, Ks 2

The following table specifies how many instances of each main class were labelled:

| Hp 0 (HV) | Hp 1  | Hp 2  | Vr 0  | Vr 1  | Vr 2  | Hp 0 (Ks) | Ks 1  | Ks 2  |
| --------- | ----- | ----- | ----- | ----- | ----- | --------- | ----- | ----- |
| 1147      | 727   | 554   | 1055  | 789   | 528   | 560       | 1077  | 614   |
| 4.4 %     | 2.8 % | 2.2 % | 4.1 % | 3.1 % | 2.1 % | 2.2 %     | 4.2 % | 2.4 % |

Nevertheless many more signal types were labelled to obtain a complete dataset regarding german mainline railway signals. When training models with the dataset it can be helpful to also have classes for very similar looking objects in order to reduce False Positives e.g. when signal backsides are visible. Therefore backsides of signals and signs, turned off signals as well as traffic lights and signs have been labelled. The following figure shows all classes and their corresponding amount of labelled instances.

![](distribution.png)

For each image we also added information about the weather and light condition which distributes as follows:

| Unknown | Sunny | Cloudy | Rainy  | Snowy | Foggy |
| ------- | ----- | ------ | ------ | ----- | ----- |
| 121     | 962   | 1746   | 457    | 164   | 112   |
| 3.4 %   | 27 %  | 49 %   | 12.8 % | 4.6 % | 3.1%  |

<sub><sup>Unknown weather tag is used for pictures at night or in tunnels*</sup></sub>

| Daylight | Twilight | Dark  |
| -------- | -------- | ----- |
| 2148     | 1228     | 186   |
| 60.3 %   | 34.5 %   | 5.2 % |

What is not (yet) included or currently in progress of labelling:

- Hl Signals (Not yet planned)

  

### Data format

For easy data handling and revision the annotations come in the PASCAL VOC format. This format consists of individual XML-files for every image containing all labelled instances and additional information like width and height of the image. All further information that does not comply with the PASCAL VOC format is saved in the info.json (e.g. weather, light, source url). The PASCAL VOC uses a "difficult" tag for each annotation. For this case the difficult tag was used to indicate if the signal was relevant to the train conductor in that situation

The images come in the .jpg format and are either 1280x720 or 1920x1080.

### How the data was gathered

The individual frames were created from video recordings from cab view rides which have been uploaded to YouTube. We asked the uploaders for permission to use their video material for our dataset. Microsofts video annotation tool [VoTT](https://github.com/microsoft/VoTT) was used to find and annotate relevant frames, in a second the step the images and annotations were revised and checked with [LabelImg](https://github.com/tzutalin/labelImg)

<!-- GETTING STARTED -->
## Getting Started

1. Install git ([Instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))

2. Clone the repo

   ```sh
   git clone https://git.rwth-aachen.de/IFS/gersign.git
   ```

   

3. The example.py and utils package include some python code to help you load the annotations

<!-- ROADMAP -->

## Roadmap

2. Gather more images to include more instances of rarely occurring signals
3. Include Hl system

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->

## Contributing

You are welcome to contribute to the dataset. The following steps guide you through process of contributing and give tips for data labelling

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewImages`)
3. Gather your images. Use only material where you have the rights to edit and republish the raw material! The YouTubers listed under [Contributors](#contributors) already gave us their permissions, so you do not need to ask again if you want to use some videos of them. If you use material from different sources please send us some proof that you and we are allowed to use, edit and publish the frames created. 
4. Annotate your images (e.g using VoTT and labelImg). Label your images completely, meaning every class that already occurs in the dataset needs to be labelled in your images as well. If you want to add a new class (e.g. a new sign or signal) you are welcome to do so. Keep mind that new classes have to be labelled in all existing images as well in order to not confuse object detectors (E.g. you want to label switches in your new images, then you have to label all switches in the existing images)
5. Add your .jpg images to the "JPEGImages" Folder and annotations (in the PASCAL VOC XML Format) to the "Annotations" Folder
6. For each frame add all additional information (weather, light, author, author url, source url) to the info.json
7. Commit your Changes (`git commit -m 'Added some new annotated images'`)
8. Push to the Branch (`git push origin feature/NewImages`)
9. Open a Pull Request, we will then review your added images and try to merge them into the dataset.

## Contributors

We would like to thank all YouTubers by supporting us with their cab view recordings and kindly allow us to use their material. The following YouTubers contributed their material to our dataset:

- [Tf on Tour](https://www.youtube.com/channel/UC-IVgRwev81WZ5J9CN9T--A)
- [Ananas 747](https://www.youtube.com/channel/UCNLlR8wGbXNVVT_IAwI8qpg)
- [German Express Driver](https://www.youtube.com/channel/UCgfJB0BN0x2qYqqpple5OOw)
- [Rotausleuchtung](https://www.youtube.com/channel/UCZXB_WOu2iSYZeWj1C4p2Zg)(Response pending!)

<!-- LICENSE -->
## License

<p xmlns:dct="http://purl.org/dc/terms/" xmlns:cc="http://creativecommons.org/ns#" class="license-text"><span rel="dct:title">The GERSign Dataset</span> by <span property="cc:attributionName">Philipp Leibner and Fabian Hampel</span> is licensed under 
<a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0">CC BY-SA 4.0
<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" />
<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" />
<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1" />
</a>
</p>



<!-- CONTACT -->
## Contact

Philipp Leibner - philipp.leibner@ifs.rwth-aachen.de 	Fabian Hampel - fabian.hampel@ifs.rwth-aachen.de

<div>  
<a href="">
    <img src="http://www.ifs.rwth-aachen.de/fileadmin/images/rwth_ifs_de_rgb.png" alt="IFS Logo" width="400">
  </a>
</div>

<!-- ACKNOWLEDGEMENTS -->

## Related Dataset
* [RailSem19](https://wilddash.cc/railsem19) (For general semantic scene understanding of railway related scenes)
* [FRSign](https://frsign.irt-systemx.fr/) (Dataset for French railway signals)
* [COCO](https://cocodataset.org/#home) (Includes bounding boxes for trains, cars and traffic lights (treats railway signals as traffic lights))





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=flat-square
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=flat-square
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=flat-square
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=flat-square
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=flat-square
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[example-screenshot]: example.png